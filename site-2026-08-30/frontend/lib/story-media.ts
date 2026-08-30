export const HERO_IMAGE = "/covers/hero-newsroom.png";

export const EDITORIAL_COVERS = [
  "/covers/cover-neural-lab.png",
  "/covers/cover-city-ai.png",
  "/covers/cover-servers.png",
  "/covers/cover-library.png",
  "/covers/cover-chip.png",
  "/covers/cover-code-desk.png",
  "/covers/cover-research-hands.png",
] as const;

function hashKey(value: string): number {
  let hash = 0;
  for (const character of value) {
    hash = (hash * 31 + character.charCodeAt(0)) >>> 0;
  }
  return hash;
}

export function storyCover(story: { slug: string; hero_image_url: string | null }): string {
  if (story.hero_image_url) {
    return story.hero_image_url;
  }
  return EDITORIAL_COVERS[hashKey(story.slug) % EDITORIAL_COVERS.length];
}

export function catalogCover(slug: string): string {
  return EDITORIAL_COVERS[hashKey(slug) % EDITORIAL_COVERS.length];
}
