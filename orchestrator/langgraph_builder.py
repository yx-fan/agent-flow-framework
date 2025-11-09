import os
import yaml
import inspect
from langgraph.graph import StateGraph
from core.logger import get_logger, log_info, log_error, log_debug, log_warning
from core.registry import AgentRegistry, NodeRegistry
from orchestrator.reflection_node import ReflectionNode
from orchestrator.feedback_manager import FeedbackManager
from core.exceptions import ConfigError, NodeError

logger = get_logger("LangGraphBuilder")


class LangGraphBuilder:
    """
    Dynamically builds LangGraph workflows from YAML configuration files.
    Supports multi-domain workflows under data/<domain>/workflows/*.yaml.
    """

    def __init__(self, base_dir: str = "data", default_domain: str = "hello"):
        self.base_dir = base_dir
        self.default_domain = default_domain
        log_info("LangGraphBuilder initialized.", base_dir=self.base_dir, default_domain=self.default_domain)

    # Load workflow configuration for a domain
    def load_config(self, domain: str) -> dict:
        """
        Load YAML workflow configuration for the given domain.
        Example: data/dealer/workflows/dealer_workflow.yaml
        """
        domain = domain or self.default_domain
        workflow_dir = os.path.join(self.base_dir, domain, "workflows")

        # default naming convention: <domain>_workflow.yaml
        default_filename = f"{domain}_workflow.yaml"
        config_path = os.path.join(workflow_dir, default_filename)

        if not os.path.exists(config_path):
            log_warning("Workflow file not found; using default domain.", domain=domain, path=config_path)
            # fallback to default domain workflow
            config_path = os.path.join(self.base_dir, self.default_domain, "workflows", f"{self.default_domain}_workflow.yaml")

        if not os.path.exists(config_path):
            log_error("Workflow configuration file not found.", path=config_path)
            raise ConfigError(f"Workflow file not found for domain '{domain}'")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                log_debug("Workflow configuration loaded.", domain=domain, path=config_path)
                return data
        except Exception as e:
            log_error("Failed to load workflow configuration.", domain=domain, path=config_path, error=str(e))
            raise ConfigError("Failed to load workflow configuration.") from e

    # Build workflow graph
    async def build_graph(self, intent: str, domain: str) -> StateGraph:
        """
        Build a LangGraph workflow for the specified intent and domain.
        """
        config = self.load_config(domain)
        flow = config.get(intent)

        if not flow:
            raise ConfigError(f"No workflow found for intent '{intent}' in domain '{domain}'")

        g = StateGraph(dict)
        log_info("Building graph for intent.", domain=domain, intent=intent)

        nodes = flow.get("nodes", [])
        edges = flow.get("edges", [])

        # ---- Nodes ----
        for node in nodes:
            node_name = node.get("name")
            node_type = node.get("type")
            class_name = node.get("class")

            if not node_name or not node_type or not class_name:
                log_warning("Invalid node config entry skipped.", node=node)
                continue

            try:
                handler = await self._resolve_handler(node_type, class_name)
                if not inspect.iscoroutinefunction(handler):
                    async def async_wrapper(inputs, h=handler):
                        return h(inputs)
                    g.add_node(node_name, async_wrapper)
                else:
                    g.add_node(node_name, handler)

            except Exception as e:
                raise NodeError(f"Failed to initialize node '{node_name}' in domain '{domain}': {e}") from e

        # ---- Edges ----
        for edge in edges:
            if isinstance(edge, list):
                if len(edge) == 2:
                    src, dest = edge
                    g.add_edge(src, dest)
                elif len(edge) == 3 and "if:" in edge[2]:
                    src, dest, cond_str = edge
                    cond_key = cond_str.replace("if:", "").strip()
                    g.add_conditional_edges(src, {cond_key: dest})
                else:
                    log_warning("Invalid edge format; skipped.", edge=edge)
            else:
                log_warning("Edge entry is not a list; skipped.", edge=edge)

        if nodes:
            first_node = nodes[0]["name"]
            g.set_entry_point(first_node)

        log_info("LangGraph build complete.", domain=domain, intent=intent, nodes=len(nodes), edges=len(edges))
        return g

    # Internal helper
    async def _resolve_handler(self, node_type: str, class_name: str):
        """Resolve and instantiate the correct node handler."""
        if node_type == "agent":
            agent_cls = AgentRegistry.get(class_name)
            if not agent_cls:
                raise ValueError(f"Agent class '{class_name}' not registered.")
            return agent_cls().run

        elif node_type == "node":
            if class_name == "ReflectionNode":
                return ReflectionNode().run
            elif class_name == "FeedbackManager":
                return FeedbackManager().collect_feedback
            else:
                custom_node_cls = NodeRegistry.get(class_name)
                if not custom_node_cls:
                    raise ValueError(f"Custom node '{class_name}' not registered.")
                return custom_node_cls().execute

        raise ValueError(f"Unknown node type '{node_type}'")
