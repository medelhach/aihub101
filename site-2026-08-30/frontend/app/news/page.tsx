import { StoryCard } from "@/components/content/story-card";
import { listNews, type StorySummary } from "@/services/api";

export const metadata = {
  title: "AI News",
  description: "Structured briefs on consequential AI developments.",
};

export default async function NewsPage() {
  let items: StorySummary[] = [];
  try {
    items = (await listNews(24)).items;
  } catch {
    items = [];
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
      {items.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-sm text-slate-600">
          No news briefs yet. Run the content-cycle worker to ingest live feeds.
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
