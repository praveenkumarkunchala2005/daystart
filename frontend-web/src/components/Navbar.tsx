"use client";

import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { SITE_NAME } from "@/lib/types";

const VISIBLE_COUNT = 7;

interface NavbarProps {
  categories: string[];
}

export function Navbar({ categories }: NavbarProps) {
  // State for search input
  const [search, setSearch] = useState("");
  // State for mobile menu visibility
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  // State for "More" categories dropdown
  const [moreOpen, setMoreOpen] = useState(false);
  // State for filtering categories in the "More" dropdown
  const [catSearch, setCatSearch] = useState("");
  const moreRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Split categories into visible and overflow (hidden in "More" menu)
  const visibleCats = categories.slice(0, VISIBLE_COUNT);
  const overflowCats = categories.slice(VISIBLE_COUNT);
  
  // Filter overflow categories based on search input within the "More" menu
  const filteredCats = catSearch.trim()
    ? categories.filter((c) => c.toLowerCase().includes(catSearch.toLowerCase()))
    : overflowCats;

  // Effect to close the "More" dropdown when clicking outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) {
        setMoreOpen(false);
        setCatSearch("");
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Handle main search form submission
  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (search.trim()) {
      router.push(`/search?q=${encodeURIComponent(search.trim())}`);
      setSearch("");
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <Image src="/logo.svg" alt={SITE_NAME} width={28} height={28} className="rounded-md" />
          <span className="font-brand text-xl font-bold tracking-tight text-black">
            {SITE_NAME}
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <form onSubmit={handleSearch} className="hidden sm:block">
            <div className="relative">
              <svg
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <input
                type="text"
                placeholder="Search articles..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-44 rounded-md border border-neutral-200 bg-neutral-50 py-2 pl-10 pr-4 text-sm text-black placeholder-neutral-400 transition-all focus:w-60 focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
              />
            </div>
          </form>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="rounded-md p-2 text-neutral-600 hover:bg-neutral-100 md:hidden"
            aria-label="Toggle menu"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Category bar */}
      <div className="border-y border-neutral-200 relative z-[100]">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <nav className="hidden-scrollbar flex items-center justify-center gap-1 overflow-x-auto py-2">
            {visibleCats.map((cat) => (
              <Link
                key={cat}
                href={`/category/${encodeURIComponent(cat)}`}
                className="whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium text-neutral-600 transition-colors hover:bg-neutral-100 hover:text-black"
              >
                {cat}
              </Link>
            ))}

            {overflowCats.length > 0 && (
              <div className="relative" ref={moreRef}>
                <button
                  type="button"
                  onClick={() => {
                    setMoreOpen((v) => !v);
                    setCatSearch("");
                  }}
                  className={`flex items-center gap-1 whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${moreOpen
                      ? "bg-neutral-900 text-white"
                      : "text-neutral-600 hover:bg-neutral-100 hover:text-black"
                    }`}
                >
                  {/* More */}
                  {/* <svg
                    className={`h-3 w-3 transition-transform ${moreOpen ? "rotate-180" : ""
                      }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg> */}
                </button>

                
              </div>
            )}
          </nav>
        </div>
      </div>


      {mobileMenuOpen && (
        <div className="border-b border-neutral-200 bg-white px-4 py-4 md:hidden">
          <form onSubmit={handleSearch} className="mb-4">
            <input
              type="text"
              placeholder="Search articles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-md border border-neutral-200 bg-neutral-50 px-4 py-2 text-sm text-black placeholder-neutral-400 focus:border-black focus:outline-none focus:ring-1 focus:ring-black"
            />
          </form>
          <nav className="flex flex-col gap-3">
            {categories.map((cat) => (
              <Link
                key={cat}
                href={`/category/${encodeURIComponent(cat)}`}
                onClick={() => setMobileMenuOpen(false)}
                className="text-sm font-medium text-neutral-500 transition-colors hover:text-black"
              >
                {cat}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
