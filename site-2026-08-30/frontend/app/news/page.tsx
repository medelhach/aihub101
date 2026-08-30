import { StoryCard } from "@/components/content/story-card";
import { listNews, type StorySummary } from "@/services/api";

export const metadata = {
  title: "AI News",
  description: "Structured briefs on consequential AI developments.",
};

export default async function NewsPage() {
  let items: StorySummary[] = [];
  let loadError: string | null = null;
  try {
    items = (await listNews(24)).items;
  } catch (error) {
    loadError = error instanceof Error ? error.message : "Failed to load news.";
  }

  return (
    <div className="flex w-full flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">News</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          Automated, source-attributed briefs from outlets such as MIT Technology Review,
          TechCrunch, OpenAI, Google, WIRED, and Ars Technica. Each item is structured like a
          news report and links back to the original publisher.
        </p>
      </header>
      {loadError ? (
        <p className="rounded-2xl border border-dashed border-red-200 bg-white p-8 text-sm text-slate-600">
          {loadError}
        </p>
      ) : items.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-sm text-slate-600">
          No news briefs yet. Restart the API so editorial seed stories can load, then wait for
          the content-cycle worker.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((story) => (
            <StoryCard key={story.slug} story={story} />
          ))}
        </div>
      )}
    </div>
  );
}
