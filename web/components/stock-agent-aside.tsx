import { getAgentStatus } from "@/lib/agent-config";
import { StockAgentDrawer } from "@/components/stock-agent-drawer";

export function StockAgentAside({ code }: { code: string }) {
  const status = getAgentStatus();

  if (!status.enabled) {
    return null;
  }

  return <StockAgentDrawer code={code} />;
}
