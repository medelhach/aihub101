import { StoryIndex } from "@/components/content/story-index";
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
    <StoryIndex
      title="Articles"
      kicker="Long reads"
      description="Research notes, lab posts, and technical explainers from Hugging Face, DeepMind, Meta AI, NVIDIA, AWS, Microsoft Research, and arXiv."
      banner="/covers/cover-library.png"
      items={items}
      loadError={loadError}
      empty="No articles yet. Restart the API so editorial seed stories can load, then wait for the content-cycle worker."
    />
  );
}
