export function StockPageHeader({
  code,
  name,
}: {
  code: string;
  name: string;
}) {
  return (
    <header className="pt-2">
      <h1 className="text-[32px] font-bold leading-tight tracking-tight text-on-surface">
        {name}
      </h1>
      <p className="mt-1 text-sm text-on-surface-variant">{code}</p>
    </header>
  );
}

export function quoteToHeaderProps(
  code: string,
  quot?: Record<string, string> | null,
) {
  return {
    code,
    name: quot?.name || code,
  };
}
