import Link from 'next/link';

interface HeaderProps {
  variant?: 'light' | 'dark';
}

export default function Header({ variant = 'light' }: HeaderProps) {
  const isDark = variant === 'dark';
  
  return (
    <div className="fixed top-0 left-0 right-0 w-full z-50">
      <div className="h-16 flex">
        <div className={`${isDark ? 'bg-black' : 'bg-white'} flex-1 flex items-center justify-end px-8`}>
          <div className="flex items-center space-x-4">
            <Link href="/auth/register" className={`px-6 py-2 text-sm font-normal ${isDark ? 'text-red-400 bg-black border-red-400 hover:bg-gray-900' : 'text-red-600 bg-white border-red-600 hover:bg-red-50'} border transition-colors rounded-md`}>
              REGISTER
            </Link>
            <Link href="/auth/login" className="px-6 py-2 text-sm font-normal bg-blue-600 text-white hover:bg-blue-700 transition-colors rounded-md">
              LOGIN
            </Link>
          </div>
        </div>
      </div>
      <div className={`w-full border-b ${isDark ? 'border-gray-700' : 'border-gray-300'}`} style={{ borderWidth: '0.5px' }}></div>
    </div>
  );
}