// app/layout.js
import "../styles/globals.css";

export const metadata = {
  title: "Movie App",
  description: "Browse classic films & chat about them",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head />
      <body>{children}</body>
    </html>
  );
}