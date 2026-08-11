import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Painting Christmas With You — Interactive Storyboard",
  description: "A synchronized local storyboard and screenplay reader.",
  manifest: "/manifest.webmanifest",
  themeColor: "#17191c",
  appleWebApp: { capable: true, title: "PCWY Boards", statusBarStyle: "black-translucent" },
  icons: { icon: "/pwa-192.png", apple: "/pwa-192.png" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
