import Link from 'next/link';
import Header from '@/components/layout/Header';

export default function Home() {
  return (
    <>
      <Header variant="dark" />
      <main className="min-h-screen bg-white dark:bg-[#111111] pt-16">

      <div className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center mb-20">
          <h1 className="text-6xl font-bold text-black mb-6">
            PAY A REWARD<br />NOT A RANSOM
          </h1>
          <p className="text-xl text-gray-600 mb-10">
            Global Bug Bounty & Vulnerability Management Platform
          </p>
          
          <div className="flex justify-center gap-4">
            <Link href="/auth/register" className="px-8 py-4 bg-secondary text-white text-lg font-medium rounded-full hover:bg-secondary-hover transition-colors">
              CONTACT US
            </Link>
            <Link href="/auth/login" className="px-8 py-4 bg-primary text-white text-lg font-medium rounded-full hover:bg-primary-hover transition-colors">
              START HUNTING
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="border-2 border-black p-8">
            <h3 className="text-2xl font-bold text-black mb-3">Bug Bounty</h3>
            <p className="text-gray-600">
              Find vulnerabilities and earn rewards from top organizations
            </p>
          </div>

          <div className="border-2 border-black p-8">
            <h3 className="text-2xl font-bold text-black mb-3">PTaaS</h3>
            <p className="text-gray-600">
              Professional penetration testing services with expert researchers
            </p>
          </div>

          <div className="border-2 border-black p-8">
            <h3 className="text-2xl font-bold text-black mb-3">Learning Platform</h3>
            <p className="text-gray-600">
              Practice your skills in our simulation environment
            </p>
          </div>
        </div>
      </div>
      </main>
    </>
  );
}
