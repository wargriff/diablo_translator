import { cn } from "@/lib/utils";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
};

export function PageHeader({ title, subtitle, action, className }: PageHeaderProps) {
  return (
    <header className={cn("mb-8 flex flex-wrap items-end justify-between gap-4", className)}>
      <div>
        <p className="d4-subtitle mb-1">Diablo Translator</p>
        <h1 className="d4-title">{title}</h1>
        {subtitle ? <p className="mt-2 text-sm text-diablo-muted">{subtitle}</p> : null}
      </div>
      {action}
    </header>
  );
}
