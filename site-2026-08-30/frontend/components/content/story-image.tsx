import { storyCover } from "@/lib/story-media";
import { cn } from "@/lib/utils";
import type { StorySummary } from "@/services/api";

type StoryImageProps = {
  story: Pick<StorySummary, "slug" | "headline" | "hero_image_url">;
  className?: string;
  priority?: boolean;
};

export function StoryImage({ story, className, priority }: StoryImageProps) {
  return (
    // Remote RSS images and local covers both land here; native img avoids a remote allowlist.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={storyCover(story)}
      alt=""
      className={cn("h-full w-full object-cover", className)}
      fetchPriority={priority ? "high" : "auto"}
    />
  );
}
