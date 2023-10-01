import moviepy.editor as mp
import librosa
import matplotlib.pyplot as plt
import argparse


def ezcut(
    input_file="audiotest2.mkv",
    chunk_length=0.01,
    window_length=0.5,
    thresh=0.003,
    min_clip_size=1.5,
    graph_me=False,
):
    """
    Opens an input video, and saves a copy with
    the quiet sections cut out, as .mp4 .
    General algorithm:
    1 Break down video into small chunks of specified length
    2 calculate the loudness of each chunk
    3 calculate the max chunk loudness for a window around each chunk
    4 apply a threshold to these, label everything as good or bad
    5 iterate over the chunks to get timestamps of contiguous matching chunks
    6 stich together only the good meta-chunks

    Args:
        input_file (str): Location of video to cut up.
        chunk_length (float, optional): in seconds. Defaults to 0.01.
        window_length (float, optional): length of mask in seconds.
            Defaults to 0.5.
        thresh (float, optional): cut out chunks quieter than this.
            Defaults to 0.003.
        min_clip_size (float, optional): cut out chunks shorter than this.
            Defaults to 1.5.
        graph_me (bool, optional): if True, function will instead create
            a graph previewing the cuts. Defaults to False.
    """
    output_file = "out/" + input_file[: input_file.rfind(".")] + "_cut.mp4"
    print("Loading video file")
    video = mp.VideoFileClip(input_file)
    a = video.audio
    num_loops = video.duration // chunk_length

    loudness = [
        print(f"Calculating loudness: {i/num_loops:.0%}", end="\r")
        or librosa.feature.rms(chunk)[0]
        for i, chunk in enumerate(a.iter_chunks(chunk_duration=chunk_length))
    ]

    max_loudness = max(loudness)
    window_size = int(window_length // chunk_length)

    window = [
        max(loudness[max(0, i - window_size):(i + window_size)])
        for i in range(len(loudness))
    ]

    list_of_clips = []
    clip_on = True
    start_time = 0
    print("Analyzing...")
    for i in range(len(window)):
        if window[i] >= thresh:  # then clip should be on
            if not clip_on:  # start of a new clip
                clip_on = True
                start_time = i * chunk_length
        else:  # then clip should be off
            if clip_on:  # end of current clip
                clip_on = False
                end_time = (i - 1) * chunk_length
                if end_time - start_time >= min_clip_size:
                    list_of_clips += ((start_time, end_time),)

    if graph_me:
        time = [i * chunk_length for i in range(len(loudness))]
        plt.plot(time, loudness, label="actual sound")
        plt.plot(time, window, color="orange", label="mask")
        plt.axhline(thresh, linestyle=":", color="green")
        for clip in list_of_clips:
            plt.plot(clip, [max_loudness] * 2, color="green")
            plt.text(
                sum(clip) / 2,
                max_loudness * 1.015,
                str(round(clip[1] - clip[0], 1)),
                ha="center",
                color="green",
            )
        # don't mind this next line, I'm just getting the legend element:
        plt.plot(clip, [max_loudness] * 2, color="green", label="clips")

        plt.ylabel("Loudness")
        plt.xlabel("Time")
        plt.legend()
        plt.show()

    else:
        print("Compiling output...")
        final = mp.concatenate_videoclips(
            [video.subclip(i[0], i[1]) for i in list_of_clips]
        )
        final.write_videofile(output_file, codec="libx264")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copies a video but with the quiet sections cut out.")

    parser.add_argument("file", type=str, help="Input filepath")
    parser.add_argument("--chunk", type=float,
                        help="Sample time, in s", default=0.01)
    parser.add_argument("--window", type=float,
                        help="Mask length, in s", default=0.5)
    parser.add_argument("--thresh", type=float, default=0.003,
                        help="Min loudness")
    parser.add_argument("--min_clip", type=float, default=1.5,
                        help="Min length of a subclip to keep, in s")
    parser.add_argument("-g", "--graph", action="store_true",
                        help="If True, preview the cuts instead.")

    args = parser.parse_args()
    ezcut(input_file=args.file, chunk_length=args.chunk,
          window_length=args.window, thresh=args.thresh,
          min_clip_size=args.min_clip, graph_me=args.graph)


