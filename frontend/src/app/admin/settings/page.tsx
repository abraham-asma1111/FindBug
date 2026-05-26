import { redirect } from 'next/navigation';

export default function SettingsPage() {
  // Redirect to the first category by default
  redirect('/admin/settings/access-control');
}
