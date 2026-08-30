import { StoryCard } from "@/components/content/story-card";
import { listArticles, type StorySummary } from "@/services/api";

export const metadata = {
  title: "AI Articles",
  description: "Longer explainers from labs, cloud blogs, and research feeds.",
};

export default async function ArticlesPage() {
  let items: StorySummary[] = [];
  let loadError: string | null = null;
  try {
    items = (await listArticles(24)).items;
  } catch (error) {
    loadError = error instanceof Error ? error.message : "Failed to load articles.";
  }

  return (
    <div className="flex w-full flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">Articles</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          Research notes, lab posts, and technical explainers from Hugging Face, DeepMind,
          Meta AI, NVIDIA, AWS, Microsoft Research, and arXiv.
        </p>
      </header>
      {loadError ? (
        <p className="rounded-2xl border border-dashed border-red-200 bg-white p-8 text-sm text-slate-600">
          {loadError}
        </p>
      ) : items.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-sm text-slate-600">
          No articles yet. Restart the API so editorial seed stories can load, then wait for the
          content-cycle worker.
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
