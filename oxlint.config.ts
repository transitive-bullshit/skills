import base from '@fisch0920/config/oxlint'
import manifest from './skills.json' with { type: 'json' }

export default {
  ...base,
  ignorePatterns: [
    ...(base.ignorePatterns ?? []),
    'provenance/**',
    ...Object.entries(manifest.skills)
      .filter(([, skill]) => skill.origin.kind !== 'personal')
      .map(([name]) => `skills/${name}/**`)
  ]
}
