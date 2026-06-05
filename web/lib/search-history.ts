export type RecentStock = {
  code: string;
  name: string;
};

const STORAGE_KEY = "twelvewin:recent-stocks";
const MAX_RECENT = 8;

export function getRecentStocks(): RecentStock[] {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw) as RecentStock[];
    if (!Array.isArray(parsed)) {
      return [];
    }
    return parsed.filter(
      (item) =>
        item &&
        typeof item.code === "string" &&
        typeof item.name === "string",
    );
  } catch {
    return [];
  }
}

export function addRecentStock(stock: RecentStock): void {
  if (typeof window === "undefined") {
    return;
  }

  const normalized: RecentStock = {
    code: stock.code.trim(),
    name: stock.name.trim() || stock.code.trim(),
  };
  if (!normalized.code) {
    return;
  }

  const existing = getRecentStocks().filter(
    (item) => item.code !== normalized.code,
  );
  const next = [normalized, ...existing].slice(0, MAX_RECENT);

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Ignore quota or privacy mode errors.
  }
}
