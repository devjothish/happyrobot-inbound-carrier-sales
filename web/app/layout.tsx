import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Carrier Sales — Broker Console",
  description:
    "Inbound carrier sales dashboard. Built for HappyRobot FDE take-home.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
