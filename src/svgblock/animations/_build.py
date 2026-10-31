from ._base import BaseAnimation, Keyframe, Layer, Pose


def _pose_css(pose: Pose) -> str:
    return (
        f"opacity: {pose.opacity:g}; "
        f"transform: translate({pose.x:g}px, {pose.y:g}px) scale({pose.scale:g});"
    )


def _percent(fraction: float) -> str:
    return f"{fraction * 100:.6f}".rstrip("0").rstrip(".")


def _keyframe_css(keyframe: Keyframe) -> str:
    timing = (f" animation-timing-function: {keyframe.easing.css()};"
              if keyframe.easing else "")
    return f"{_percent(keyframe.at)}% {{ {_pose_css(keyframe.pose)}{timing} }}"


def _keyframes_css(layer: Layer) -> str:
    steps = " ".join(_keyframe_css(keyframe) for keyframe in layer.keyframes)
    return f"@keyframes {layer.name} {{\n{steps}\n}}"


def _animation_value(layer: Layer) -> str:
    count = "infinite" if layer.iterations is None else layer.iterations
    return (f"{layer.name} {layer.duration:g}s {layer.easing.css()} "
            f"{layer.delay:g}s {count} {layer.fill}")


def build_animation_css(animation: BaseAnimation) -> str:
    layers = animation.layers()
    if not layers:
        return ""

    name = animation.css_name
    keyframes = "\n".join(_keyframes_css(layer) for layer in layers)
    value = ", ".join(_animation_value(layer) for layer in layers)

    return f"""
{keyframes}
.{name} {{
  animation: {value};
  transform-box: fill-box;
  transform-origin: center;
}}
@media (prefers-reduced-motion: reduce) {{
  .{name} {{ animation: none; }}
}}
"""
