export function normalizeSearchCode(input: string): string | null {
  const token = input.trim().split(/\s+/)[0];
  if (!token) {
    return null;
  }

  const withoutSuffix = token.replace(/\.(SH|SZ)$/i, "");
  const digits = withoutSuffix.replace(/^(sz|sh)/i, "");
  if (/^\d{6}$/.test(digits)) {
    return digits;
  }

  return null;
}

export function looksLikeStockCode(input: string): boolean {
  return normalizeSearchCode(input) !== null;
}
