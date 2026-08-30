import { StoryCard } from "@/components/content/story-card";
import type { StorySummary } from "@/services/api";

type StoryIndexProps = {
  title: string;
  kicker: string;
  description: string;
  banner: string;
  items: StorySummary[];
  loadError: string | null;
  empty: string;
};

export function StoryIndex({
  title,
  kicker,
  description,
  banner,
  items,
  loadError,
  empty,
}: StoryIndexProps) {
  const [lead, ...rest] = items;

  return (
    <div className="mx-auto flex w-full max-w-[1280px] flex-col gap-10 px-4 py-8 sm:px-6 lg:px-8">
      <header className="border-b border-rule pb-6">
        <p className="text-[0.7rem] font-semibold tracking-[0.32em] text-crimson uppercase">{kicker}</p>
        <h1 className="font-display mt-2 text-4xl tracking-tight md:text-5xl">{title}</h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-ink/70">{description}</p>
      </header>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={banner} alt="" className="aspect-[21/8] w-full object-cover" />
      {loadError ? (
        <p className="border border-crimson/30 bg-cream p-8 text-sm text-ink/70">{loadError}</p>
      ) : items.length === 0 ? (
        <p className="border border-dashed border-rule bg-cream p-8 text-sm text-ink/70">{empty}</p>
      ) : (
        <>
          <StoryCard story={lead} variant="feature" />
          {rest.length > 0 ? (
            <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
              {rest.map((story) => (
                <StoryCard key={story.slug} story={story} />
              ))}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

