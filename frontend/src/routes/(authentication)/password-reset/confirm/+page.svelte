<script lang="ts">
	import type { PageData } from './$types';
	import Logo from '$lib/components/Logo/Logo.svelte';
	import SuperForm from '$lib/components/Forms/Form.svelte';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import { ResetPasswordSchema } from '$lib/utils/schemas';
	import { zod4 as zod } from 'sveltekit-superforms/adapters';
	import { m } from '$paraglide/messages';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
</script>

<div class="min-h-screen w-full bg-slate-200 px-4 py-6 sm:px-6">
	<div class="flex justify-center sm:absolute sm:top-5 sm:left-5">
		<div class="flex flex-row max-w-40 sm:max-w-48 space-x-4 pb-3">
			<Logo />
		</div>
	</div>
	<div class="flex min-h-[calc(100vh-8rem)] w-full items-center justify-center">
		<div
			class="flex flex-col w-full max-w-md bg-white p-5 sm:p-8 lg:p-12 rounded-lg shadow-lg items-center space-y-4"
		>
			<div class="bg-primary-300 px-6 py-5 rounded-full text-3xl">
				<i class="fa-solid fa-key"></i>
			</div>
			<p class="text-gray-600 text-sm text-center">
				{m.resetPasswordHere()}<br />
			</p>
			<!-- SuperForm with dataType 'form' -->
			<div class="flex w-full">
				<SuperForm
					class="flex flex-col space-y-3 w-full"
					data={data?.form}
					dataType="form"
					validators={zod(ResetPasswordSchema)}
				>
					{#snippet children({ form })}
						<TextField type="password" {form} field="new_password" label={m.newPassword()} />
						<TextField
							type="password"
							{form}
							field="confirm_new_password"
							label={m.confirmNewPassword()}
						/>
						<p class="pt-3">
							<button
								class="btn preset-filled-primary-500 font-semibold w-full"
								type="submit"
								data-testid="set-password-btn">{m.resetPassword()}</button
							>
						</p>
					{/snippet}
				</SuperForm>
			</div>
		</div>
	</div>
</div>
