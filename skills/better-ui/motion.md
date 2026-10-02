# Shared motion guidance

Use this reference for motion authoring, review, and planning. User requirements and the established project design system take precedence over the illustrative defaults here. Accessibility, observable correctness, and measured performance remain evidence requirements; a different aesthetic value is not automatically a defect.

## Purpose and frequency

Motion should clarify feedback, state, continuity, or an intentional expressive moment. Frequent actions deserve immediate usable feedback; a subtle transition can still be appropriate if it does not delay input or comprehension. Keyboard initiation alone does not make motion wrong. Static feedback is a valid choice.

## Timing and continuity

Reuse existing easing and duration tokens. When none exist, start with brief responsive transitions and tune them against the actual interaction. Ease-out often suits entrances, ease-in-out suits movement between positions, and linear suits constant progress. These are defaults, not a ban on other curves.

An opacity-only transition can be sufficient. Add scale or translation when it conveys useful continuity; preserve a logical origin for trigger-attached surfaces. Stagger only when sequence helps comprehension and never delay interaction for decoration.

Rapid or reversible actions should retarget smoothly from their current state. Choose transitions, springs, or cancellable timelines according to the actual interruption behavior. Test rapid toggles, reversals, and gesture release; do not infer behavior from the animation mechanism alone.

## Accessibility

Honor reduced-motion preferences with gentler motion or no animation as appropriate. Preserve state and feedback through static text, icons, color with another cue, or focus. Essential information must remain available without movement. Gate hover-only effects to suitable pointer devices; keep touch and keyboard feedback usable.

## Performance

Prefer transform and opacity for visual motion when they preserve geometry, hit testing, and neighboring layout. Layout transitions can be appropriate when layout change is the behavior; measure their cost. Specify intended transition properties. Investigate unintended transitions, layout thrashing, persistent offscreen loops, and measured frame drops rather than treating every syntax pattern as proof of jank.

Use the installed library's current API and version. A Motion shorthand, CSS keyframe, blur, or particular curve is not independently proof of a performance defect. Add compositing hints only to address observed need and avoid unnecessary persistent layers.

## Verification and reporting

Inspect the changed interaction at normal speed and, when helpful, slowed playback. Check interruption, relevant input methods, and reduced motion. For a review, report the source location, evidence, consequence, and smallest correction; separate defects from optional taste changes and state verification limits.

Read [animations.md](animations.md) for press/theme recipes, [enter-exit.md](enter-exit.md) for staged transitions, [icon-transitions.md](icon-transitions.md) for icon examples, and [performance.md](performance.md) for implementation checks only when needed. Recipe values are starting points and yield to the project's system.
