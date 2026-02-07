import { notFound } from "next/navigation";
import { getArticleBySlug, getRelatedArticles } from "@/lib/queries";
import { ArticleContent } from "@/components/ArticleContent";
import { ArticleList } from "@/components/ArticleList";
import { CategoryBadge } from "@/components/CategoryBadge";
import { TagList } from "@/components/TagList";
import { format } from "date-fns";
import type { Metadata } from "next";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticleBySlug(slug);
  if (!article) return { title: "Article Not Found" };
  return {
    title: article.Title,
    description: article.Summary || undefined,
  };
}

export default async function ArticlePage({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticleBySlug(slug);
  if (!article) notFound();

  const related = await getRelatedArticles(article);

  return (
    <article className="mx-auto max-w-4xl">
        {article["Image URL"] && article["Image URL"].trim() !== "" && (
          <div className="mb-8 overflow-hidden rounded-md bg-black">
            <img
              src={article["Image URL"]}
              alt={article.Title}
              className="h-[400px] w-full object-cover bg-black"
            />
        </div>
      )}

      <div className="mb-6 flex flex-wrap items-center gap-3">
        {article.Category && <CategoryBadge category={article.Category} />}
          <time className="text-sm text-neutral-400" dateTime={article.created_at} suppressHydrationWarning>
          {format(new Date(article.created_at), "MMMM d, yyyy")}
        </time>
      </div>

      <h1 className="mb-6 text-3xl font-bold leading-tight text-black sm:text-4xl lg:text-5xl">
        {article.Title}
      </h1>

      {article.Summary && (
        <p className="mb-8 text-xl leading-relaxed text-neutral-500">
          {article.Summary}
        </p>
      )}

      {article.Content && <ArticleContent html={article.Content} />}

      {article.Tags && article.Tags.length > 0 && (
        <div className="mt-10 border-t border-neutral-200 pt-6">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-widest text-neutral-400">
            Tags
          </h3>
          <TagList tags={article.Tags} />
        </div>
      )}

      {related.length > 0 && (
        <section className="mt-16">
          <h2 className="mb-6 text-2xl font-bold text-black">
            Related Articles
          </h2>
          <ArticleList articles={related} />
        </section>
      )}
    </article>
  );
}
