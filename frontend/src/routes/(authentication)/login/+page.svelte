<script lang="ts">
	import type { ActionData, PageData } from './$types';
	import Logo from '$lib/components/Logo/Logo.svelte';
	import Greetings from './Greetings.svelte';
	import FormCard from './FormCard.svelte';

	interface Props {
		data: PageData;
		form: ActionData;
	}

	let { data, form }: Props = $props();
</script>

<div class="lg:relative min-h-screen bg-slate-200 px-4 py-6 sm:px-6 lg:p-0">
	<div class="lg:absolute top-5 lg:left-5 flex justify-center">
		<div class="flex justify-center flex-row max-w-40 sm:max-w-48 space-x-4 pb-3">
			<Logo />
		</div>
	</div>
	<div
		class="lg:absolute lg:top-1/2 lg:left-1/2 w-full transform lg:-translate-x-1/2 lg:-translate-y-1/2"
	>
		<div
			class="flex flex-col lg:flex-row w-full lg:pr-8 gap-6 lg:gap-4 min-h-[calc(100vh-8rem)] lg:min-h-0 justify-center"
		>
			<Greetings />
			<div class="flex justify-center lg:pr-5 items-center w-full lg:w-2/5">
				<FormCard {data} {form} />
			</div>
		</div>
	</div>
</div>
