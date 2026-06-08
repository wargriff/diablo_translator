"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function HomePage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/reply");
  }, [router]);

  return (
    <div className="flex min-h-[40vh] items-center justify-center text-diablo-muted">
      <Link href="/reply" className="text-diablo-gold hover:underline">
        Ouvrir la traduction…
      </Link>
    </div>
  );
}
