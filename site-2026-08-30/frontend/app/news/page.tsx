import { StoryIndex } from "@/components/content/story-index";
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
    <StoryIndex
      title="News"
      kicker="The desk"
      description="Automated, source-attributed briefs from outlets such as MIT Technology Review, TechCrunch, OpenAI, Google, WIRED, and Ars Technica. Each item is structured like a news report and links back to the original publisher."
      banner="/covers/cover-city-ai.png"
      items={items}
      loadError={loadError}
      empty="No news briefs yet. Restart the API so editorial seed stories can load, then wait for the content-cycle worker."
    />
  );
}
