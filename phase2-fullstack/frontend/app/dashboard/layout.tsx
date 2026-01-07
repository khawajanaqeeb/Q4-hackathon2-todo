import { AuthProvider } from '../../context/AuthContext';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Authentication is handled by AuthContext (client-side)
  // and the dashboard page itself checks for user data
  return (
    <AuthProvider>
      <div>{children}</div>
    </AuthProvider>
  );
}