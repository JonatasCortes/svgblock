from ._base import BaseAnimation, Pose


def _pose_css(pose: Pose) -> str:
    return (
        f"opacity: {pose.opacity:g}; "
        f"transform: translate({pose.x:g}px, {pose.y:g}px) scale({pose.scale:g});"
    )


def build_animation_css(animation: BaseAnimation) -> str:
    name = animation.css_name
    steps = " ".join(
        f"{keyframe.at * 100:g}% {{ {_pose_css(keyframe.pose)} }}"
        for keyframe in animation.keyframes()
    )
    count = "infinite" if animation.iterations is None else animation.iterations

    return f"""
@keyframes {name} {{
  {steps}
}}
.{name} {{
  animation: {name} {animation.duration:g}s {animation.easing} {count} both;
  transform-box: fill-box;
  transform-origin: center;
}}
@media (prefers-reduced-motion: reduce) {{
  .{name} {{ animation: none; }}
}}
"""
