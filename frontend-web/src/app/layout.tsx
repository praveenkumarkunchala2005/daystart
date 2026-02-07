import type { Metadata } from "next";
import { Poppins, Bricolage_Grotesque } from "next/font/google";
import "./globals.css";
import { VisualEditsMessenger } from "orchids-visual-edits";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { getAllCategories, getAllTags } from "@/lib/queries";
import { SITE_NAME, SITE_DESCRIPTION } from "@/lib/types";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-poppins",
});

const bricolage = Bricolage_Grotesque({
  subsets: ["latin"],
  weight: ["700"],
  variable: "--font-bricolage",
});

export const metadata: Metadata = {
  title: {
    default: SITE_NAME,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [categories, tags] = await Promise.all([
    getAllCategories(),
    getAllTags(),
  ]);

  return (
    <html lang="en">
      <body
        className={`${poppins.variable} ${bricolage.variable} font-sans antialiased`}
      >
        <Navbar categories={categories} />
        <main className="mx-auto min-h-screen max-w-7xl px-4 py-8 sm:px-6">
          {children}
        </main>
        <Footer categories={categories} tags={tags} />
        <VisualEditsMessenger />
      </body>
    </html>
  );
}
