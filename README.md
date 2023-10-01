EZCut is a command-line tool to remove numerous quiet sections from a video with the minimal amount of effort.

When recording, leave a small amount of silence at the start and end of the video, as these sections may be cut reagrdless of their content.

Dependencies: moviepy, librosa, matplotlib

TODO:
- Improve handling of good chunks at start/end of input video
- Add another parameter that is a buffer added to loud sections, distinct from the window size
(the reason this is complicated is this might make windows collide)

