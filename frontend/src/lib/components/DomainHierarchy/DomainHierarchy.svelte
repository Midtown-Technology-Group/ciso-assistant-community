<script lang="ts">
	import Anchor from '$lib/components/Anchor/Anchor.svelte';
	import { safeTranslate } from '$lib/utils/i18n';
	import { m } from '$paraglide/messages';
	import { onMount } from 'svelte';

	type DomainNode = {
		name: string;
		uuid: string;
		content_type: string;
		children?: DomainNode[];
	};

	type DomainRow = {
		id: string;
		name: string;
		type: string;
		depth: number;
		path: string[];
		childCount: number;
	};

	let rows = $state<DomainRow[]>([]);
	let isLoading = $state(true);
	let loadFailed = $state(false);

	function flattenDomainTree(node: DomainNode, path: string[] = [], depth = 0): DomainRow[] {
		const children = node.children ?? [];
		const visibleChildren = children.filter((child) => ['DO', 'GL'].includes(child.content_type));
		const current =
			node.content_type === 'DO' || node.content_type === 'GL'
				? [
						{
							id: node.uuid,
							name: node.name,
							type: node.content_type,
							depth,
							path,
							childCount: visibleChildren.length
						}
					]
				: [];
		return [
			...current,
			...visibleChildren.flatMap((child) =>
				flattenDomainTree(child, [...path, node.name], depth + 1)
			)
		];
	}

	onMount(() => {
		fetch('/folders/org_tree/?include_perimeters=false')
			.then((response) => {
				if (!response.ok) throw new Error('Failed to load domain hierarchy');
				return response.json();
			})
			.then((tree: DomainNode) => {
				rows = flattenDomainTree(tree).slice(0, 12);
			})
			.catch(() => {
				loadFailed = true;
			})
			.finally(() => {
				isLoading = false;
			});
	});
</script>

<section class="mb-4 border-y border-surface-200 py-3 dark:border-surface-700">
	<div class="mb-2 flex flex-wrap items-center justify-between gap-2">
		<div>
			<h2 class="text-base font-semibold text-surface-950 dark:text-surface-50">
				{m.domains()}
				{safeTranslate('parentDomain').toLowerCase()}
			</h2>
			<p class="text-xs text-surface-600 dark:text-surface-300">
				{safeTranslate('serviceProvider')} -> {safeTranslate('customerChildren')} /
				{safeTranslate('mtgInternal')}
			</p>
		</div>
		<Anchor
			href="/x-rays/inspect"
			class="btn-mini-secondary inline-flex items-center gap-2 px-3 py-2 text-sm"
			label={m.inspect()}
		>
			<i class="fa-solid fa-diagram-project"></i>
			<span>{m.inspect()}</span>
		</Anchor>
	</div>

	{#if isLoading}
		<div class="text-sm text-surface-600 dark:text-surface-300">{safeTranslate('loading')}...</div>
	{:else if loadFailed}
		<div class="text-sm text-error-700 dark:text-error-300">{safeTranslate('error')}</div>
	{:else if rows.length === 0}
		<div class="text-sm text-surface-600 dark:text-surface-300">
			{safeTranslate('noResultsFound')}
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="text-xs uppercase text-surface-500 dark:text-surface-400">
					<tr>
						<th class="py-2 font-medium">{m.domains()}</th>
						<th class="py-2 font-medium">{safeTranslate('parentDomain')}</th>
						<th class="py-2 font-medium">{safeTranslate('contentType')}</th>
						<th class="py-2 text-right font-medium">{safeTranslate('customerChildren')}</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-surface-100 dark:divide-surface-800">
					{#each rows as row (row.id)}
						<tr class="text-surface-900 dark:text-surface-100">
							<td class="py-2">
								<a
									href="/folders/{row.id}"
									class="inline-flex items-center gap-2 hover:text-primary-700 dark:hover:text-primary-200"
									style:padding-left={`${Math.min(row.depth, 6) * 1.1}rem`}
								>
									<i class="fa-solid fa-folder-tree text-xs text-surface-400"></i>
									<span>{row.name}</span>
								</a>
							</td>
							<td class="py-2 text-surface-600 dark:text-surface-300">
								{row.path.at(-1) ?? '-'}
							</td>
							<td class="py-2 text-surface-600 dark:text-surface-300">{row.type}</td>
							<td class="py-2 text-right tabular-nums text-surface-600 dark:text-surface-300">
								{row.childCount}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</section>
