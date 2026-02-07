import Link from "next/link";
import Image from "next/image";
import { SITE_NAME } from "@/lib/types";

export function Footer({ categories, tags }: { categories: string[]; tags: string[] }) {
  return (
    <footer className="mt-16 border-t border-neutral-200 bg-neutral-50">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <Link href="/" className="flex items-center gap-2.5">
                <Image src="/logo.svg" alt={SITE_NAME} width={24} height={24} className="rounded-md" />
              <span className="font-brand text-lg font-bold tracking-tight text-black">
                {SITE_NAME}
              </span>
            </Link>
            <p className="mt-3 text-sm leading-relaxed text-neutral-500">
              Stories, insights, and news about founders and startups.
            </p>
          </div>

          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-black">
              Categories
            </h3>
            <nav className="flex flex-col gap-2">
                {categories.map((cat) => (
                <Link
                  key={cat}
                  href={`/category/${encodeURIComponent(cat)}`}
                  className="text-sm text-neutral-500 transition-colors hover:text-black"
                >
                  {cat}
                </Link>
              ))}
            </nav>
          </div>

          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-black">
              Popular Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {tags.slice(0, 8).map((tag) => (
                <Link
                  key={tag}
                  href={`/tag/${encodeURIComponent(tag)}`}
                  className="rounded-md border border-neutral-200 bg-white px-2.5 py-1 text-xs text-neutral-500 transition-colors hover:border-black hover:text-black"
                >
                  #{tag}
                </Link>
              ))}
            </div>
          </div>

          <div>
            <h3 className="mb-4 text-xs font-semibold uppercase tracking-widest text-black">
              Links
            </h3>
            <nav className="flex flex-col gap-2">
              <Link href="/" className="text-sm text-neutral-500 transition-colors hover:text-black">
                Home
              </Link>
              <Link href="/sitemap.xml" className="text-sm text-neutral-500 transition-colors hover:text-black">
                Sitemap
              </Link>
              <Link href="/rss.xml" className="text-sm text-neutral-500 transition-colors hover:text-black">
                RSS Feed
              </Link>
            </nav>
          </div>
        </div>

        <div className="mt-10 border-t border-neutral-200 pt-6 text-center text-sm text-neutral-400">
          {"\u00A9"} 2026 {SITE_NAME}. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
