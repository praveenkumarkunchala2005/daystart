import Link from "next/link";

interface CategoryBadgeProps {
  category: string;
  variant?: "default" | "light";
}

export function CategoryBadge({ category, variant = "default" }: CategoryBadgeProps) {
  return (
    <Link
      href={`/category/${encodeURIComponent(category)}`}
      className={`inline-block rounded-md px-3 py-1 text-xs font-medium transition-colors ${
        variant === "light"
          ? "bg-white/15 text-white hover:bg-white/25"
          : "bg-neutral-100 text-black hover:bg-neutral-200"
      }`}
    >
      {category}
    </Link>
  );
}
