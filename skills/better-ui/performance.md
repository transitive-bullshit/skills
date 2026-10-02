# Motion performance checks

Use [shared motion guidance](motion.md) for the decision rules. Prefer explicit transition properties so unrelated style changes do not animate unexpectedly. Reuse the project's Tailwind/CSS conventions.

Prefer transform and opacity for visual movement when they preserve layout and hit testing. If size or layout change is part of the requested behavior, keep the intended behavior and measure the cost rather than replacing it blindly.

Investigate repeated layout reads/writes, expensive effects, unnecessary continuous work, and unintended transitions with runtime evidence. Compositing depends on the browser, property, content, and implementation; syntax alone does not establish smoothness or jank.

Add a specific `will-change` hint only when it improves an observed problem. Avoid broad or persistent hints across many elements and release temporary ones when the interaction is over. Verify the changed interaction on the relevant browser/device and report measurement limits.
