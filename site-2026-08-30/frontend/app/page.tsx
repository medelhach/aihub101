import Link from "next/link";
import type { ReactNode } from "react";

import { ModelCard } from "@/components/content/model-card";
import { StoryCard } from "@/components/content/story-card";
import { listArticles, listModels, listNews } from "@/services/api";

async function loadHome() {
  try {
    const [news, articles, models] = await Promise.all([
      listNews(4),
      listArticles(4),
      listModels(),
    ]);
    return { news: news.items, articles: articles.items, models: models.slice(0, 8) };
  } catch {
    return { news: [], articles: [], models: [] };
  }
}

export default async function Home() {
  const { news, articles, models } = await loadHome();

  return (
    <div className="flex w-full flex-col gap-16">
      <section className="max-w-3xl">
        <p className="text-sm font-medium tracking-[0.2em] text-slate-500 uppercase">
          AI Intelligence Hub
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
          What changed in AI, why it matters, and which models to use.
        </h1>
        <p className="mt-5 text-lg leading-8 text-slate-600">
          Automated briefs from established publishers, longer explainers from labs and
          research feeds, and a structured catalog of more than fifty important AI models
          with a side-by-side comparison dashboard.
        </p>
      </section>

      <HomeSection
        title="News"
        href="/news"
        empty="The news worker has not published a brief yet. Start the stack and wait for the first content cycle."
      >
        {news.map((story) => (
          <StoryCard key={story.slug} story={story} />
        ))}
      </HomeSection>

      <HomeSection
        title="Articles"
        href="/articles"
        empty="Research and lab articles will appear after the first ingestion cycle."
      >
        {articles.map((story) => (
          <StoryCard key={story.slug} story={story} />
        ))}
      </HomeSection>

      <HomeSection
        title="AI models"
        href="/models"
        empty="The model catalog seeds when the API starts against PostgreSQL."
      >
        {models.map((model) => (
          <ModelCard key={model.slug} model={model} />
        ))}
      </HomeSection>
    </div>
  );
}

function HomeSection({
  title,
  href,
  empty,
  children,
}: {
  title: string;
  href: string;
  empty: string;
  children: ReactNode;
}) {
  const hasItems = Array.isArray(children) ? children.length > 0 : Boolean(children);
  return (
    <section>
      <div className="mb-6 flex items-end justify-between gap-4">
        <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
        <Link href={href} className="text-sm font-medium text-slate-700 hover:underline">
          View all
        </Link>
      </div>
      {hasItems ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{children}</div>
      ) : (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-sm text-slate-600">
          {empty}
        </p>
      )}
    </section>
  );
}
