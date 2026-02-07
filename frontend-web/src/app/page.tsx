import { getArticles } from "@/lib/queries";
import { HeroBanner } from "@/components/HeroBanner";
import { ArticleList } from "@/components/ArticleList";
import { Pagination } from "@/components/Pagination";
import { ARTICLES_PER_PAGE } from "@/lib/types";

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page: pageParam } = await searchParams;
  const page = Number(pageParam) || 1;
  const { articles, count } = await getArticles(page);
  const totalPages = Math.ceil(count / ARTICLES_PER_PAGE);

  const heroArticle = page === 1 ? articles[0] : null;
  const gridArticles = page === 1 ? articles.slice(1) : articles;

  return (
    <>
      {heroArticle && <HeroBanner article={heroArticle} />}

      <section>
        <h2 className="mb-6 text-2xl font-bold text-black">
            {page === 1 ? "Latest Articles" : `Articles — Page ${page}`}
        </h2>
        <ArticleList articles={gridArticles} />
        <Pagination currentPage={page} totalPages={totalPages} basePath="/" />
      </section>
    </>
  );
}
