const DEFAULT_COMMERCIAL_ORIGIN = "http://localhost:3001";

export function getCommercialOrigin() {
  return (
    process.env.NEXT_PUBLIC_COMMERCIAL_URL?.trim().replace(/\/$/, "") ||
    DEFAULT_COMMERCIAL_ORIGIN
  );
}

export function getCommercialPricingUrl() {
  return (
    process.env.NEXT_PUBLIC_COMMERCIAL_PRICING_URL?.trim() ||
    `${getCommercialOrigin()}/pricing`
  );
}
