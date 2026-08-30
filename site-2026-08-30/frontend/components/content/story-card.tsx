import Link from "next/link";

import { formatDate, type StorySummary } from "@/services/api";

type StoryCardProps = {
  story: StorySummary;
};

export function StoryCard({ story }: StoryCardProps) {
  const href = `/${story.section}/${story.slug}`;
  return (
    <article className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="text-xs font-semibold tracking-[0.18em] text-slate-500 uppercase">
        {story.source_name}
      </p>
      <h2 className="mt-2 text-xl font-semibold tracking-tight text-slate-950">
        <Link href={href} className="hover:underline">
          {story.headline}
        </Link>
      </h2>
      <p className="mt-3 flex-1 text-sm leading-6 text-slate-600">{story.dek}</p>
      <p className="mt-4 text-xs text-slate-500">
        {formatDate(story.published_at)} · {story.word_count} words
      </p>
    </article>
  );
}
