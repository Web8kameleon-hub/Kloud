import type { Metadata } from 'next';

export const metadata: Metadata = {
	title: 'Music Studio - Clisonix',
	description: 'Create music with do-re-mi notes, sine waveform and WAV export.',
	appleWebApp: {
		capable: true,
		title: 'Music Studio',
		statusBarStyle: 'black-translucent',
	},
};

export default function MusicStudioLayout({ children }: { children: React.ReactNode }) {
	return <>{children}</>;
}
