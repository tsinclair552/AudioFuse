# Spec Document for application AudioFuse.

This is a desktop application that takes two audio clips as input and returns a third audio clip comprised of the combined two clips.

## Interface

There are two windows in the app, side-by-side, labeled 'Clip 1' and 'Clip 2' and a toggle button labeled 'Pause' and a button labeled Download.

If the Pause toggle is activated,  a 1 second silent audio clip will be inserted between the first and second input clips. The output clip will then consist of the first clip, followed by 1 second of silent audio, followed by the second clip.

If the Pause toggle is not activated, the output clip will consist of the two input clips only.

The first clip will be loaded into the left-side window and the second will be loaded into the right-side window.

The Download clip will allow the user to save the combined clip in a location of their choosing.

