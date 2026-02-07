export function ArticleContent({ html }: { html: string }) {
  return (
    <div
      className="prose prose-lg max-w-none prose-headings:font-bold prose-headings:text-black prose-p:text-neutral-600 prose-p:leading-relaxed prose-a:text-black prose-a:underline hover:prose-a:text-neutral-500 prose-strong:text-black prose-img:rounded-md"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
