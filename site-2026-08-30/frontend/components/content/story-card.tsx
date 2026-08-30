import Link from "next/link";

import { StoryImage } from "@/components/content/story-image";
import { cn } from "@/lib/utils";
import { formatDate, type StorySummary } from "@/services/api";

type StoryCardProps = {
  story: StorySummary;
  variant?: "feature" | "standard" | "compact";
};

export function StoryCard({ story, variant = "standard" }: StoryCardProps) {
  const href = `/${story.section}/${story.slug}`;
  const kicker = story.section === "news" ? "News" : "Article";

  if (variant === "feature") {
    return (
      <article className="group relative min-h-[28rem] overflow-hidden rounded-none md:min-h-[34rem]">
        <StoryImage story={story} className="absolute inset-0" priority />
        <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/55 to-ink/10" />
        <div className="relative flex h-full min-h-[28rem] flex-col justify-end p-6 text-paper md:min-h-[34rem] md:p-10">
          <p className="text-[0.7rem] font-semibold tracking-[0.28em] text-crimson-soft uppercase">
            {kicker} · {story.source_name}
          </p>
          <h2 className="font-display mt-3 max-w-3xl text-3xl leading-tight text-balance md:text-5xl">
            <Link href={href} className="decoration-crimson/80 underline-offset-4 hover:underline">
              {story.headline}
            </Link>
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-7 text-paper/85">{story.dek}</p>
          <p className="mt-5 text-xs tracking-wide text-paper/70">
            {formatDate(story.published_at)} · {story.word_count} words
          </p>
        </div>
      </article>
    );
  }

  if (variant === "compact") {
    return (
      <article className="group grid grid-cols-[7.5rem_1fr] gap-4 border-b border-rule py-4 last:border-b-0">
        <Link href={href} className="block overflow-hidden">
          <StoryImage story={story} className="aspect-[4/3] h-24 w-full" />
        </Link>
        <div>
          <p className="text-[0.65rem] font-semibold tracking-[0.22em] text-crimson uppercase">
            {story.source_name}
          </p>
          <h2 className="font-display mt-1 text-lg leading-snug">
            <Link href={href} className="hover:text-crimson">
              {story.headline}
            </Link>
          </h2>
          <p className="mt-1 text-xs text-ink/55">{formatDate(story.published_at)}</p>
        </div>
      </article>
    );
  }

  return (
    <article className={cn("group flex h-full flex-col overflow-hidden bg-cream")}>
      <Link href={href} className="block overflow-hidden">
        <StoryImage
          story={story}
          className="aspect-[16/10] transition duration-500 group-hover:scale-[1.03]"
        />
      </Link>
      <div className="flex flex-1 flex-col border border-t-0 border-rule px-5 py-5">
        <p className="text-[0.65rem] font-semibold tracking-[0.24em] text-crimson uppercase">
          {kicker} · {story.source_name}
        </p>
        <h2 className="font-display mt-2 text-2xl leading-snug text-balance">
          <Link href={href} className="hover:text-crimson">
            {story.headline}
          </Link>
        </h2>
        <p className="mt-3 flex-1 text-sm leading-6 text-ink/70">{story.dek}</p>
        <p className="mt-4 text-xs tracking-wide text-ink/50">
          {formatDate(story.published_at)} · {story.word_count} words
        </p>
      </div>
    </article>
  );
}
