from mcp_instance import mcp

# Importing each module causes its @mcp.tool() decorators to register
# against the shared mcp instance above.
import tools.generation  # noqa: F401
import tools.models      # noqa: F401
import tools.assets      # noqa: F401
import tools.control     # noqa: F401

if __name__ == "__main__":
    mcp.run()
