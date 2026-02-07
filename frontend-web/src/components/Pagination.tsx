import Link from "next/link";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  basePath: string;
}

/**
 * Generates an array of page numbers and ellipsis for pagination.
 *
 * @param {number} current - Current page number.
 * @param {number} total - Total number of pages.
 * @returns {(number | "ellipsis")[]} Array of page numbers and "ellipsis" markers.
 */
function getPageNumbers(current: number, total: number): (number | "ellipsis")[] {
  // If total pages are few, show all
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  const pages: (number | "ellipsis")[] = [1];

  // Add ellipsis if current page is far from start
  if (current > 3) {
    pages.push("ellipsis");
  }

  // Show pages around the current page
  const start = Math.max(2, current - 1);
  const end = Math.min(total - 1, current + 1);

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  // Add ellipsis if current page is far from end
  if (current < total - 2) {
    pages.push("ellipsis");
  }

  pages.push(total);

  return pages;
}

/**
 * Pagination component to navigate through pages.
 *
 * @param {Object} props - Component props.
 * @param {number} props.currentPage - The current active page.
 * @param {number} props.totalPages - Total number of pages available.
 * @param {string} props.basePath - Base URL path for pagination links.
 */
export function Pagination({ currentPage, totalPages, basePath }: PaginationProps) {
  if (totalPages <= 1) return null;

  const separator = basePath.includes("?") ? "&" : "?";
  const pageNumbers = getPageNumbers(currentPage, totalPages);

  return (
    <nav className="mt-12 flex items-center justify-center gap-2" aria-label="Pagination">
      {currentPage > 1 && (
        <Link
          href={`${basePath}${separator}page=${currentPage - 1}`}
          className="rounded-md border border-neutral-200 px-4 py-2 text-sm font-medium text-neutral-600 transition-colors hover:border-black hover:text-black"
        >
          Previous
        </Link>
      )}
      {pageNumbers.map((page, i) =>
        page === "ellipsis" ? (
          <span
            key={`ellipsis-${i}`}
            className="px-2 py-2 text-sm text-neutral-400"
          >
            &hellip;
          </span>
        ) : (
          <Link
            key={page}
            href={`${basePath}${separator}page=${page}`}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              page === currentPage
                ? "bg-black text-white"
                : "border border-neutral-200 text-neutral-600 hover:border-black hover:text-black"
            }`}
          >
            {page}
          </Link>
        )
      )}
      {currentPage < totalPages && (
        <Link
          href={`${basePath}${separator}page=${currentPage + 1}`}
          className="rounded-md border border-neutral-200 px-4 py-2 text-sm font-medium text-neutral-600 transition-colors hover:border-black hover:text-black"
        >
          Next
        </Link>
      )}
    </nav>
  );
}
