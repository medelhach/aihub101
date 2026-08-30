import Link from "next/link";

import { StoryCard } from "@/components/content/story-card";
import { HERO_IMAGE } from "@/lib/story-media";
import { listArticles, listModels, listNews, type ModelSummary, type StorySummary } from "@/services/api";

async function loadHome() {
  try {
    const [news, articles, models] = await Promise.all([
      listNews(8),
      listArticles(6),
      listModels(),
    ]);
    return { news: news.items, articles: articles.items, models: models.slice(0, 6) };
  } catch {
    return { news: [] as StorySummary[], articles: [] as StorySummary[], models: [] as ModelSummary[] };
  }
}

export default async function Home() {
  const { news, articles, models } = await loadHome();
  const [lead, ...moreNews] = news;
  const sidebar = moreNews.slice(0, 4);
  const restNews = moreNews.slice(4);

  return (
    <div>
      {lead ? (
        <StoryCard story={lead} variant="feature" />
      ) : (
        <section className="relative min-h-[28rem] overflow-hidden md:min-h-[34rem]">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={HERO_IMAGE} alt="" className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/50 to-ink/15" />
          <div className="relative mx-auto flex min-h-[28rem] max-w-[1280px] flex-col justify-end px-4 py-10 text-paper md:min-h-[34rem] sm:px-6 lg:px-8">
            <p className="text-[0.7rem] font-semibold tracking-[0.28em] text-crimson-soft uppercase">
              Front page
            </p>
            <h1 className="font-display mt-3 max-w-3xl text-4xl leading-tight md:text-6xl">
              The day&apos;s AI briefing, written like a newspaper.
            </h1>
            <p className="mt-4 max-w-xl text-base leading-7 text-paper/80">
              News briefs, longer explainers, and a model catalog — start the API against
              PostgreSQL to fill this desk.
            </p>
          </div>
        </section>
      )}

      <div className="mx-auto w-full max-w-[1280px] px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-12 lg:grid-cols-[minmax(0,2fr)_minmax(16rem,1fr)]">
          <section className={moreNews.length > 4 ? "" : "lg:col-span-2"}>
            <SectionHead title="The rest of the news" href="/news" />
            {moreNews.length === 0 ? (
              <EmptyNote text="News briefs appear after the API seeds editorial stories." />
            ) : (
              <div className="grid gap-8 sm:grid-cols-2">
                {(moreNews.length > 4 ? restNews : moreNews).map((story) => (
                  <StoryCard key={story.slug} story={story} />
                ))}
              </div>
            )}
          </section>
          {moreNews.length > 4 ? (
            <aside>
              <SectionHead title="Latest" href="/news" />
              <div className="border-t border-rule">
                {sidebar.map((story) => (
                  <StoryCard key={story.slug} story={story} variant="compact" />
                ))}
              </div>
            </aside>
          ) : null}
        </div>

        <section className="mt-16">
          <SectionHead title="Long reads" href="/articles" />
          {articles.length === 0 ? (
            <EmptyNote text="Articles appear after editorial seed or the research-feed cycle." />
          ) : (
            <div className="grid gap-8 md:grid-cols-3">
              {articles.map((story) => (
                <StoryCard key={story.slug} story={story} />
              ))}
            </div>
          )}
        </section>

        <section className="mt-16">
          <SectionHead title="In the model catalog" href="/models" />
          {models.length === 0 ? (
            <EmptyNote text="The catalog seeds when the API can reach PostgreSQL." />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {models.map((model) => (
                <Link
                  key={model.slug}
                  href={`/models/${model.slug}`}
                  className="border border-rule bg-cream p-5 hover:border-crimson"
                >
                  <p className="text-[0.65rem] tracking-[0.22em] text-crimson uppercase">
                    {model.provider}
                  </p>
                  <p className="font-display mt-2 text-xl">{model.name}</p>
                  <p className="mt-1 text-sm text-ink/60">{model.modality}</p>
                </Link>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function SectionHead({ title, href }: { title: string; href: string }) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4 border-b border-ink pb-2">
      <h2 className="font-display text-3xl tracking-tight">{title}</h2>
      <Link href={href} className="text-[0.7rem] tracking-[0.18em] text-crimson uppercase hover:underline">
        All
      </Link>
    </div>
  );
}

function EmptyNote({ text }: { text: string }) {
  return <p className="border border-dashed border-rule bg-cream p-6 text-sm text-ink/65">{text}</p>;
}
