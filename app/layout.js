export const metadata = {
  title: "AITUBE",
  description: "AI Video Automation System",
};

export default function RootLayout({ children }) {
  return (
    <html lang="tr">
      <body style={{ margin: 0 }}>
        {children}
      </body>
    </html>
  );
}
