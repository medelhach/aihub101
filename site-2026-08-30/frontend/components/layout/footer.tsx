export function Footer() {
  return (
    <footer className="mt-16 border-t border-rule bg-ink text-paper/80">
      <div className="mx-auto grid w-full max-w-[1280px] gap-8 px-4 py-10 sm:grid-cols-3 sm:px-6 lg:px-8">
        <div>
          <p className="font-display text-2xl text-paper">The Intelligence Desk</p>
          <p className="mt-3 text-sm leading-6">
            Structured news briefs and research explainers, always linked back to the original
            publisher.
          </p>
        </div>
        <p className="text-sm leading-6">
          Photography on this site includes original editorial covers and, when feeds provide them,
          source images. Specs in the model catalog are public figures and can change.
        </p>
        <p className="text-sm leading-6">
          Source URLs remain canonical. This desk rewrites attributed facts; it does not reprint
          full articles.
        </p>
      </div>
    </footer>
  );
}
