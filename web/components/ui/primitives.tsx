import Link from "next/link";
import type { ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "outline";

const variantClasses: Record<ButtonVariant, string> = {
  primary: "btn-gradient-primary hover:opacity-90",
  secondary:
    "bg-surface-container-highest text-on-surface hover:bg-surface-container-high",
  ghost:
    "bg-transparent text-on-surface-variant hover:text-on-surface",
  outline:
    "bg-transparent text-on-surface ghost-outline hover:bg-surface-container-highest",
};

export function Button({
  href,
  variant = "primary",
  className = "",
  children,
  uppercase = false,
  ...props
}: {
  href?: string;
  variant?: ButtonVariant;
  className?: string;
  children: ReactNode;
  uppercase?: boolean;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const classes = `inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-semibold transition ${uppercase ? "uppercase tracking-wider text-xs" : ""} ${variantClasses[variant]} ${className}`;

  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button type="button" className={classes} {...props}>
      {children}
    </button>
  );
}

export function Chip({
  children,
  tone = "neutral",
  className = "",
}: {
  children: ReactNode;
  tone?: "bullish" | "bearish" | "ai" | "neutral" | "gold";
  className?: string;
}) {
  const toneClasses = {
    bullish: "bg-bullish-container text-bullish",
    bearish: "bg-bearish-container text-bearish",
    ai: "bg-secondary-container/40 text-secondary",
    gold: "bg-tertiary-container/30 text-on-surface",
    neutral: "bg-surface-container-highest text-on-surface-variant",
  };

  return (
    <span
      className={`inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium tabular-nums ${toneClasses[tone]} ${className}`}
    >
      {children}
    </span>
  );
}

export function Pane({
  children,
  variant = "default",
  className = "",
}: {
  children: ReactNode;
  variant?: "default" | "recessed" | "elevated" | "active" | "glass";
  className?: string;
}) {
  const variantClasses = {
    default: "terminal-pane",
    recessed: "terminal-pane-recessed",
    elevated: "terminal-pane-elevated",
    active: "terminal-pane-active",
    glass: "glass-panel",
  };

  return (
    <div className={`${variantClasses[variant]} ${className}`}>{children}</div>
  );
}

export function TradingInput({
  className = "",
  ...props
}: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={`trading-input w-full px-3 py-2 body-sm text-on-surface placeholder:label-md outline-none ${className}`}
      {...props}
    />
  );
}
