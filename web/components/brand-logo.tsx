import Image from "next/image";

export function BrandLogo({ className }: { className?: string }) {
  return (
    <Image
      src="/logo.png"
      alt="团赢数据"
      width={1056}
      height={992}
      className={className ?? "h-8 object-contain"}
      style={{ width: "auto" }}
      priority
    />
  );
}
